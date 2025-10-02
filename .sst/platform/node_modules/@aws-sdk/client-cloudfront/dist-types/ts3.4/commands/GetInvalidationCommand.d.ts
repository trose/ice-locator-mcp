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
  GetInvalidationRequest,
  GetInvalidationResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface GetInvalidationCommandInput extends GetInvalidationRequest {}
export interface GetInvalidationCommandOutput
  extends GetInvalidationResult,
    __MetadataBearer {}
export declare class GetInvalidationCommand extends $Command<
  GetInvalidationCommandInput,
  GetInvalidationCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: GetInvalidationCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: GetInvalidationCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<GetInvalidationCommandInput, GetInvalidationCommandOutput>;
  private serialize;
  private deserialize;
}
