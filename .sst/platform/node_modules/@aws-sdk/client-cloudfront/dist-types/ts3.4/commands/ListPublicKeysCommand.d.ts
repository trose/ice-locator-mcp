import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import {
  Handler,
  HttpHandlerOptions as __HttpHandlerOptions,
  MetadataBearer as __MetadataBearer,
  MiddlewareStack,
} from "@smithy/types";
import {
  CloudFrontClientResolvedConfig,
  ServiceInputTypes,
  ServiceOutputTypes,
} from "../CloudFrontClient";
import {
  ListPublicKeysRequest,
  ListPublicKeysResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface ListPublicKeysCommandInput extends ListPublicKeysRequest {}
export interface ListPublicKeysCommandOutput
  extends ListPublicKeysResult,
    __MetadataBearer {}
export declare class ListPublicKeysCommand extends $Command<
  ListPublicKeysCommandInput,
  ListPublicKeysCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: ListPublicKeysCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: ListPublicKeysCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<ListPublicKeysCommandInput, ListPublicKeysCommandOutput>;
  private serialize;
  private deserialize;
}
