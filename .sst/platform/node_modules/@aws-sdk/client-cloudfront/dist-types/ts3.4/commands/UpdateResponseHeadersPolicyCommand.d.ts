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
  UpdateResponseHeadersPolicyRequest,
  UpdateResponseHeadersPolicyResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface UpdateResponseHeadersPolicyCommandInput
  extends UpdateResponseHeadersPolicyRequest {}
export interface UpdateResponseHeadersPolicyCommandOutput
  extends UpdateResponseHeadersPolicyResult,
    __MetadataBearer {}
export declare class UpdateResponseHeadersPolicyCommand extends $Command<
  UpdateResponseHeadersPolicyCommandInput,
  UpdateResponseHeadersPolicyCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: UpdateResponseHeadersPolicyCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: UpdateResponseHeadersPolicyCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    UpdateResponseHeadersPolicyCommandInput,
    UpdateResponseHeadersPolicyCommandOutput
  >;
  private serialize;
  private deserialize;
}
