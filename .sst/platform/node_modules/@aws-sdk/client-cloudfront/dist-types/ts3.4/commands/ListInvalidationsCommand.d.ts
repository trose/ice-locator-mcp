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
  ListInvalidationsRequest,
  ListInvalidationsResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface ListInvalidationsCommandInput
  extends ListInvalidationsRequest {}
export interface ListInvalidationsCommandOutput
  extends ListInvalidationsResult,
    __MetadataBearer {}
export declare class ListInvalidationsCommand extends $Command<
  ListInvalidationsCommandInput,
  ListInvalidationsCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: ListInvalidationsCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: ListInvalidationsCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<ListInvalidationsCommandInput, ListInvalidationsCommandOutput>;
  private serialize;
  private deserialize;
}
